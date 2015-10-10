TODO
====
* Use EngineTask for long term tasks. On console application, a
  KeyboardInterrupt results on a task.cancel() and for external process it is
  a proc.terminate() and proc.kill(). EngineTask has a wait operation.
