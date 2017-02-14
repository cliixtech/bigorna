from threading import Thread
import time
from unittest import TestCase
from unittest.mock import create_autospec

from nose.tools import istest

from bigorna.core import Bigorna, Standalone
from bigorna.tasks import TaskFactory, TaskScheduler
from bigorna.tasks.executor import Executor, Task
from bigorna.tracker import JobTracker
from bigorna.commons.event_bus import Event
from bigorna.tasks.base import task_status_changed_evt
from bigorna.cron.base import CronTab


cmd_type = 'ls'
params = {'dirname': '/home', 'submitter': 'john'}
output_tpl = "tasks/%s.out"
job_id = 'job_id'


class BigornaTest(TestCase):
    def setUp(self):
        self.tracker_mock = create_autospec(JobTracker)
        self.sched_mock = create_autospec(TaskScheduler)
        self.factory_mock = create_autospec(TaskFactory)
        self.cron_mock = create_autospec(CronTab)
        self.bigorna = Bigorna(output_tpl, self.tracker_mock, self.sched_mock,
                               self.factory_mock, self.cron_mock)

    @istest
    def submit_calls_factory(self):
        self.bigorna.submit(cmd_type, params)

        self.factory_mock.create_task_definition(cmd_type, params, output_tpl)

    @istest
    def submit_calls_job_tracker(self):
        task_def = self.factory_mock.create_task_definition.return_value

        self.bigorna.submit(cmd_type, params)

        self.tracker_mock.create_job.assert_called_once_with(task_def, 'john')

    @istest
    def submit_calls_job_tracker_with_anonymous_submitter(self):
        task_def = self.factory_mock.create_task_definition.return_value

        self.bigorna.submit(cmd_type, {'dirname': '/home'})

        self.tracker_mock.create_job.assert_called_once_with(task_def, 'anonymous')

    @istest
    def submit_returns_job_from_tracker(self):
        job = self.bigorna.submit(cmd_type, params)

        self.assertEquals(job, self.tracker_mock.create_job.return_value)

    @istest
    def submit_calls_sched(self):
        task_def = self.factory_mock.create_task_definition.return_value

        self.bigorna.submit(cmd_type, params)

        self.sched_mock.submit.assert_called_once_with(task_def)

    @istest
    def list_jobs_return_from_tracker(self):
        jobs = self.bigorna.list_jobs()

        self.tracker_mock.list_jobs.assert_called_once_with()
        self.assertEquals(jobs, self.tracker_mock.list_jobs.return_value)

    @istest
    def get_job_return_from_tracker(self):
        job = self.bigorna.get_job(job_id)

        self.tracker_mock.get_job.assert_called_once_with(job_id)
        self.assertEquals(job, self.tracker_mock.get_job.return_value)


class StandaloneTest(TestCase):
    def setUp(self):
        self.factory_mock = create_autospec(TaskFactory)
        self.executor_mock = create_autospec(Executor)
        self.bigorna = Standalone(self.executor_mock, self.factory_mock)

    @istest
    def submit_calls_factory(self):
        self.bigorna.submit(cmd_type, params)

        self.factory_mock.create_task_definition(cmd_type, params)

    @istest
    def submit_calls_executor(self):
        task_def = self.factory_mock.create_task_definition.return_value

        self.bigorna.submit(cmd_type, params)

        self.executor_mock.submit(task_def)

    @istest
    def join_waits_for_event_and_return_from_event(self):
        class T(Thread):
            def __init__(self, bigorna):
                super(T, self).__init__(daemon=True)
                self.bigorna = bigorna

            def run(self):
                time.sleep(0.5)
                task_mock = create_autospec(Task)
                task_mock.has_finished = True
                task_mock.is_success = True
                evt = Event(task_status_changed_evt, task_mock)
                self.bigorna.task_changed(evt)
        T(self.bigorna).start()
        result = self.bigorna.join()

        self.assertIs(result, True)
