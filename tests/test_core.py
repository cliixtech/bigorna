from unittest import TestCase
from unittest.mock import create_autospec

from nose.tools import istest

from bigorna.core import Bigorna
from bigorna.tasks import TaskFactory, TaskScheduler
from bigorna.tracker import JobTracker

cmd_type = 'ls'
params = {'dirname': '/home', 'submitter': 'john'}
output_tpl = "tasks/%s.out"
job_id = 'job_id'


class BigornaTest(TestCase):
    def setUp(self):
        self.tracker_mock = create_autospec(JobTracker)
        self.sched_mock = create_autospec(TaskScheduler)
        self.factory_mock = create_autospec(TaskFactory)
        self.bigorna = Bigorna(output_tpl, self.tracker_mock, self.sched_mock, self.factory_mock)

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
