from bigorna.commons import Config
from bigorna.tasks import TaskScheduler, TaskFactory
from bigorna.tracker import JobTracker, Job


class NotInitializedError(Exception):
    pass


class Bigorna:
    def __init__(self, output_tpl, tracker: JobTracker, sched: TaskScheduler, factory: TaskFactory):
        self.output = output_tpl
        self._tracker = tracker
        self._sched = sched
        self._task_factory = factory

    def submit(self, task_type, params) -> Job:
        task_def = self._task_factory.create_task_definition(task_type, params, self.output)
        job = self._tracker.create_job(task_def, params.get('submitter', 'anonymous'))
        self._sched.submit(task_def)
        return job

    def list_jobs(self):
        return self._tracker.list_jobs()

    def get_job(self, job_id) -> Job:
        return self._tracker.get_job(job_id)

    @staticmethod
    def new(cfg: Config):
        tracker = JobTracker(cfg)
        sched = TaskScheduler(cfg)
        factory = TaskFactory(cfg)
        return Bigorna(cfg.output_pattern, tracker, sched, factory)
