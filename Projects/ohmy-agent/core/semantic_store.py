import os
import yaml
import uuid
from typing import Dict, List, Optional

class SemanticStore:
    """
    Agent가 지식을 저장하고 검색하는 단일 창구(Facade).
    Phase 1: 순수 파이썬 Dictionary와 YAML/MD 파일 I/O로 동작합니다.
    추후 이 클래스 내부만 LlamaIndex 구조로 변경하면 됩니다.
    """
    
    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = workspace_dir
        self.chapters_dir = os.path.join(workspace_dir, "chapters")
        
        # 파일 경로 설정
        self.meta_file = os.path.join(workspace_dir, "playbook_meta.yaml")
        self.kb_file = os.path.join(workspace_dir, "knowledge_base.yaml")
        
        # 작업 폴더 초기화
        os.makedirs(self.chapters_dir, exist_ok=True)
        
        # 인메모리(In-memory) 데이터 저장소 (딕셔너리)
        self.playbook_data = {"book_title": "Untitled Playbook", "chapters": []}
        self.knowledge_base = []
        
        # 기존 데이터가 있으면 디스크에서 불러오기
        self._load_from_disk()

    # ---------------------------------------------------------
    # 1. BOOK & CHAPTER 관계 관리 (Entity Management)
    # ---------------------------------------------------------
    def set_book_title(self, title: str):
        """Playbook의 전체 제목을 설정합니다."""
        self.playbook_data["book_title"] = title
        self._save_to_disk()
        return f"성공: 책 제목이 '{title}'(으)로 설정되었습니다."

    def add_chapter(self, title: str, content_md: str) -> str:
        """
        새로운 Chapter를 추가합니다. 
        메타데이터는 YAML에, 실제 내용은 MD 파일로 분리 저장하여 관계를 맺습니다.
        """
        chapter_id = f"ch_{uuid.uuid4().hex[:8]}"
        filename = f"{chapter_id}.md"
        filepath = os.path.join(self.chapters_dir, filename)
        
        # 1. 실제 MD 파일 생성
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_md)
            
        # 2. BOOK-CHAPTER 관계 및 하이퍼링크 메타데이터 저장
        chapter_meta = {
            "id": chapter_id,
            "title": title,
            "file_link": f"./chapters/{filename}", # 하이퍼링크 참조용
            "status": "draft"
        }
        self.playbook_data["chapters"].append(chapter_meta)
        self._save_to_disk()
        
        return f"성공: 챕터 '{title}'이(가) 생성되었습니다. (ID: {chapter_id})"

    def update_chapter_content(self, chapter_id: str, new_content_md: str) -> str:
        """기존 Chapter의 MD 파일 내용을 수정합니다."""
        for ch in self.playbook_data["chapters"]:
            if ch["id"] == chapter_id:
                filepath = os.path.join(self.workspace_dir, ch["file_link"])
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content_md)
                return f"성공: 챕터 '{ch['title']}' 내용이 업데이트되었습니다."
        return f"실패: ID가 '{chapter_id}'인 챕터를 찾을 수 없습니다."

    # ---------------------------------------------------------
    # 2. Given-When-Then 지식 축적 및 검색 (Knowledge Base)
    # ---------------------------------------------------------
    def memorize_rule(self, given: str, when: str, then: str) -> str:
        """에이전트가 학습한 편집 가이드라인이나 룰을 축적합니다."""
        rule = {
            "id": f"rule_{uuid.uuid4().hex[:8]}",
            "given": given,
            "when": when,
            "then": then
        }
        self.knowledge_base.append(rule)
        self._save_to_disk()
        return f"성공: 새로운 지식(Rule)이 축적되었습니다."

    def recall_knowledge(self, query: str) -> str:
        """
        쿼리와 관련된 지식을 검색합니다. 
        (Phase 1: 단순 키워드 매칭 구현. 추후 Vector/Semantic Search로 교체)
        """
        results = []
        for rule in self.knowledge_base:
            # Given, When, Then 내용 중 하나라도 쿼리가 포함되어 있으면 반환
            if query.lower() in rule["given"].lower() or \
               query.lower() in rule["when"].lower() or \
               query.lower() in rule["then"].lower():
                results.append(f"- Given {rule['given']}, When {rule['when']}, Then {rule['then']}")
        
        if not results:
            return "검색 결과: 관련된 지식이 없습니다."
        return "검색된 지식 가이드라인:\n" + "\n".join(results)

    # ---------------------------------------------------------
    # 3. 내부 I/O 유틸리티 (Disk Sync)
    # ---------------------------------------------------------
    def _save_to_disk(self):
        """메모리의 딕셔너리 데이터를 YAML 파일로 덮어씁니다."""
        with open(self.meta_file, "w", encoding="utf-8") as f:
            yaml.dump(self.playbook_data, f, allow_unicode=True, sort_keys=False)
            
        with open(self.kb_file, "w", encoding="utf-8") as f:
            yaml.dump(self.knowledge_base, f, allow_unicode=True, sort_keys=False)

    def _load_from_disk(self):
        """기존에 작업하던 파일이 있으면 메모리로 불러옵니다."""
        if os.path.exists(self.meta_file):
            with open(self.meta_file, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if loaded: self.playbook_data = loaded
                
        if os.path.exists(self.kb_file):
            with open(self.kb_file, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if loaded: self.knowledge_base = loaded