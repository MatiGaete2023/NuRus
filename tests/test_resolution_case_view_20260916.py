from nurus.personal import runtime_fixes_20260916_projects as project_fix


class Words:
    def __init__(self):
        self.data={
            'a|PC_IE':('X-1','MULCHEN','PC_IE','auto'),
            'b|PC_IE':('X-1','MULCHEN','PC_IE','auto'),
            'c|PC_INFO':('X-1','MULCHEN','PC_INFO','auto'),
            'd|PC_IE':('X-2','MULCHEN','PC_IE','auto'),
        }
    def get_children(self): return tuple(self.data)
    def item(self,iid,what): return self.data[iid] if what=='values' else None
    def delete(self,iid): self.data.pop(iid)


class Summary:
    def set(self,value): self.value=value


def test_resolution_list_deduplicates_same_case_and_kind_but_keeps_other_kind(monkeypatch):
    dummy=type('Dummy',(),{})()
    dummy.words=Words();dummy.work=type('Work',(),{'rows':[]})();dummy.summary=Summary()
    monkeypatch.setattr(project_fix,'_ORIGINAL_SHOW_WORK',lambda self:None)
    project_fix.show_work_one_row_per_project(dummy)
    assert set(dummy.words.data)=={'a|PC_IE','c|PC_INFO','d|PC_IE'}
