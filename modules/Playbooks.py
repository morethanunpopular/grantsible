from pprint import pprint
import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import yaml

# initialize needed objects
class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print json.dumps({host.name: result._result}, indent=4)




# create inventory and pass to var manager

class PlayBook:
  def __init__(self,PlaybookPath,InventoryPath):
    self.InventoryPath = InventoryPath
    self.PlaybookPath = PlaybookPath
    self.results_callback = ResultCallback()
    self.variable_manager = VariableManager()
    self.loader = DataLoader()
    Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
    self.options = Options(connection='local', module_path='./modules', forks=100, become=None, become_method=None, become_user=None, check=False)
    self.passwords = dict(vault_pass='secret')
    self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.InventoryPath)
    self.variable_manager.set_inventory(self.inventory)
    with open(PlaybookPath, 'r') as fh:
      dataList = yaml.load(fh)
    data = dataList[0]
    play_source2 = {}
    for key in data.keys():
      play_source2[key] = data[key]
      play_source2['tasks'] = []
    for task in data['tasks']:
      taskDict = {}
      for module in task.keys():
       taskDict['action'] = { 'module' : module, 'args' : task[module] }
    play_source2['tasks'].append(taskDict)
    self.play = Play().load(play_source2, variable_manager=self.variable_manager, loader=self.loader)
  def runPlay(self):
    try:
      tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=self.results_callback,  # Use our custom callback instead of the ``default`` callback plugin
            )
      result = tqm.run(self.play)
    finally:
      if tqm is not None:
          tqm.cleanup()

