TODO
====
* Quan s'executa un procés extern en una operació de plataforma és recomanable
  utilitzar la funció storm.module.platform.execute, a la que se li passa una
  instància de PlatformTaskContext. Aquesta crea un Popen que va enviant la
  sortida com missatges a la cua d'esdeveniments i que fa cancel checking cada
  X segons (amb time.sleep es poden indicar fraccions de segons).
* Fer servir pipes per escriure a sortida estàndard i sortida d'error des de les
  tasques. Adéu a l'esdeveniment "message". Les tasques de l'engine escriuen a
  "None" per defecte. Els cabdells d'entrada es passen opcionalment com a
  paràmetre de cada operació de l'engine. CORRECCIÓ: Passar out i err, podent
  ser el que invoca el que faci ús de pipes.
