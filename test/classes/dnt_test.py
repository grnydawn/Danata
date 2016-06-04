''' Danata test classes '''

from __future__ import print_function
import sys

class DntTest(object):
    (NOT_EXECUTED, FAILED, PASSED) = range(3)
    TEST_NUM = 0

    def get_tasks(self):
        for taskname, taskfunc in self.task_map:
            yield self.tasks[taskname]

    def get_result(self, key, result_type='general'):
        return self.result[result_type][key]

    def set_status(self, result, taskname, status, errmsg=''):
        result[taskname]['status'] = status
        if status==self.PASSED:
            pass
        elif status==self.FAILED:
            result[taskname]['errmsg'] = errmsg
        elif status==self.NOT_EXECUTED:
            pass
        else:
            raise Exception('Unknown status: %s'%status)

    def perform_test(self):
        result = { 'general': {'passed': False, 'errmsg': [], 'mandatory_tasks': ['verify_task']} }

        self.task_map = \
            [ ('prep_task', self.preprocess), ('mkdir_task', self.mkworkdir), ('download_task', self.download), \
            ('config_task', self.config), ('read_task', self.read), ('xform_task', self.xform), \
            ('write_task', self.write), ('verify_task', self.verify), ('rmdir_task', self.rmdir), \
            ('postp_task', self.postprocess), ('_finalize_task', self._finalize) ]

        for taskname, taskfunc in self.task_map:
            result[taskname] = {}
            result[taskname]['status'] = self.NOT_EXECUTED
            result[taskname]['errmsg'] = ''

        for taskname, taskfunc in self.task_map:
            print('.', end='')
            sys.stdout.flush()

            if 'goto' in result and result['goto'] and taskname != result['goto']:
                self.set_status(result, taskname, self.PASSED)
                continue
            result['goto'] = None

            result = taskfunc(taskname, result)

            is_passed = True
            if taskname in result['general']['mandatory_tasks']:
                if result[taskname]['status'] == self.NOT_EXECUTED:
                    result[taskname]['errmsg'] = 'Mandatory task, "%s", is not executed.'%taskname
                    is_passed = False
                elif result[taskname]['status'] != self.PASSED:
                    is_passed = False
            elif result[taskname]['status'] not in [ self.NOT_EXECUTED, self.PASSED ]:
                is_passed = False

            if not is_passed:
                if taskname !='_finalize_task':
                    result = self._finalize('_finalize_task', result)
                break

            if taskname==self.STOP_AT:
                print ('Test is stopped at', taskname)
                break

        return result

    def preprocess(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def mkworkdir(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def download(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def config(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def read(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def xform(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def write(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def verify(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def rmdir(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def postprocess(self, myname, result):
        self.set_status(result, myname, self.NOT_EXECUTED)
        return result

    def _finalize(self, myname, result):
        self.set_status(result, myname, self.PASSED)
        errmsg = []
        is_passed = True
        for taskname in [ name for name, func in self.task_map ]:
            if taskname in result['general']['mandatory_tasks']:
                if result[taskname]['status'] == self.NOT_EXECUTED or \
                    result[taskname]['status'] != self.PASSED:
                    is_passed = False
            elif result[taskname]['status'] not in [ self.NOT_EXECUTED, self.PASSED ]:
                is_passed = False

            if not is_passed:
                if result[taskname]['errmsg']:
                    errmsg.append('%s: %s'%(taskname, result[taskname]['errmsg']))
        result['general']['errmsg'] = errmsg
        result['general']['passed'] = is_passed

        if is_passed: print('PASSED')
        else: print('FAILED')
        return result

