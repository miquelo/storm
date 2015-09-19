* No es treballa amb directoris, sino amb fitxers i els seus directoris.
* Tot el domini penja d'una arrel. Un mateix fitxer de configuració pot tenir
  més d'un element de diferent tipus sempre que estiguin en el mateix nivell de
  la gerarquia.
* Els fitxers s'obtenen des de qualsevol lloc, per tant cal utilitzar URI i
  mòdul resource que ho gestioni de forma transparent.
* Les plataformes es creen dins del namespace "storm.provider.platform".
* CHECK: Creació d'una imatge en un "TAR".
