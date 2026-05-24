# Entités
### `Entity`
Chaque élément qui possède une animation est de classe `Entity` ou héritière de cette dernière.
La classe `Entity` hérite de `arcade.TextureAnimationSprite` et possède comme attributs principaux une direction (`arcade.Vec2`) et une vitesse (`int | float`). Finalement la classe a une méthode `move(self) -> None` qui bouge le sprite d'un pas en fonction de la direction et de la vitesse. Cette méthode sert aussi à mettre à jour l'animation du sprite.
### `Player(Entity)`
La classe `Player` sert à modéliser notre joueur. On y stocke donc le nombre de cristaux ramassés (`int`) et la direction dans laquelle il regarde (`arcade.Vec2`). En effet, cette dernière diffère de la simple direction du joueur car quand le joueur ne bouge pas, sa direction est définie comme le vecteur nul. Il est nécessaire de stocker la direction dans laquelle le joueur regarde pour afficher la bonne animation. L'override de la fonction `move()` sert d'ailleurs à ça (en plus, bien sûr, d'appeler la méthode parent `super().move()`). <br>
De plus, cette classe possède une méthode `input(self, pressed_keys: list[bool]) -> None` qui modifie la direction en fonction des touches appuyées.
## Monstres
### `Monster(Entity)`
La classe `Monster` sert à modéliser... le suspens est à son comble... les monstres. <br>
Tous les monstres ont un domaine limité, qu'on représente par deux `arcade.Vec2`. Le domaine correspond donc au rectangle défini par ces deux points.
En règle générale les monstres ne sortent pas de leur domaine, sauf pour exception les blobs.
Les monstres ont aussi une cible (`arcade.Vec2`) et leur direction est toujours orientée vers leur cible. <br>
Finalement les monstres peuvent se faire sonner, ou "stun" en anglais. Quand un monstre est stun, la méthode `super().move()` n'est plus appelée et les monstres sont projetés en direction opposée du joueur et puis immobilisés pendant un bref instant. Puis le mouvement reprend comme auparavant.
Cette fonctionnalité de stun est seulement utilisée par le sceptre.
### `Bat(Monster)`
Les chauves-souris ont un mouvement aléatoire : elles choisissent une cible aléatoire dans leur domaine, puis une fois la cible atteinte elles en choisissent une nouvelle. Malgré la simplicité de l'algorithme cela donne un mouvement plutôt naturel.
### `Spinner(Monster)`
Les spinners peuvent se déplacer sur une ligne droite dont les bornes sont dictées par la présence de buissons. Ces limites sont donc calculées à l'initialisation en fonction de si le spinner est horizontal ou vertical.
Le domaine est alors une ligne droite et non pas un rectangle. La cible du spinner est assignée à une des bornes et une fois cette cible atteinte, la cible change de côté.
### `Blob(Monster)`
Les blobs sont clairement les monstres les plus complexes du jeu.
A l'initialisation, on calcule toutes les cases vers lesquelles il existe un chemin depuis la position de départ (dans la limite de notre frontière). Et ensuite on choisit parmi ces cases pour calculer la cible, comme pour les autres monstres, une fois la cible atteinte on choisit une nouvelle cible parmi nos cases possibles. Pour atteindre une cible, le blob se déplace sur le navmesh en utilisant des cibles temporaires intermédiaires sur chaque nœud du chemin calculé. <br>
Pour ce qui est de la détection du joueur, si le blob peut voir le joueur (information qui est relayée par le gameview) il calcule un chemin vers le joueur. Quand un blob est stun, on active une détection de collision entre lui et les murs, pour assurer qu'il ne se fasse pas propulser à travers les murs.
## Armes
La classe `Weapon(Entity)` modélise toutes les armes du jeu.
Les armes ont un propriétaire (`owner: Player`) et un état (`_state: int`).
La variable d'état est utile pour savoir ce que fait l'arme à cet instant précis (repos, en action, etc.).
### `Boomerang(Weapon)`
Le boomerang fonctionne sur 3 états.
- 0 : inactif, la position du boomerang est la même que celle du joueur et il n'est pas affiché.
- 1 : lancé, le boomerang avance en ligne droite depuis où il a été lancé.
- 2 : retour, le boomerang avance en direction du joueur jusqu'à l'atteindre.

Une fois dans l'état 1, si le boomerang touche un monstre, un mur ou s'il parcourt une certaine distance il se met dans l'état 2.
L'information de savoir si le boomerang a touché quelque chose est donnée par le gameview. La distance parcourue est calculée dans la méthode `move()` du boomerang.
### `Sword(Weapon)`
L'épée fonctionne sur 2 états.
- 0 : inactif, la position de l'épée est la même que celle du joueur et elle n'est pas affichée.
- 1 : actif, on montre l'animation et l'épée tue tous les monstres qui se trouvent dans sa hitbox.
Une fois que l'animation est terminée on retourne à l'état 0.
### `Sceptre(Weapon)`
Le sceptre est un item collectionnable.
Il est une extension et fonctionne sur 3 états :
- 0 : inactif, fonctionne comme pour l'épée.
- 1 : actif, pendant une seule frame, applique un stun à tous les monstres dans un rayon.
- 2 : fin d'animation, attend que l'animation se termine.
# Objets
### Leviers
Les leviers ne sont pas des entités, ils héritent simplement de `arcade.Sprite`. Les leviers stockent leur état (`state: bool`) et un identificateur (`id: Final[str]`). Nous reparlerons de l'identificateur plus tard.
Les leviers comportent une méthode (`toggle(self) -> None`) qui est appelée par le gameview en cas de collision.
### Portail
Les portails, comme les leviers ne sont pas des entités et héritent de `arcade.Sprite`. Ils stockent également leur état ainsi qu'une "condition d'ouverture" <br>.
Une condition est un dictionnaire à une seule entrée avec comme clé un opérateur logique (sous forme de string ; "and", "or", "not") et comme valeur une liste de deux ou un éléments qui sont eux-mêmes des conditions.
En bas de l'échelle récursive on a des leviers avec leur `id` associé.
On peut donc récursivement évaluer si un portail doit être activé ou non.

# Map
La classe `Map` représente la carte du jeu. Elle peut donc charger un fichier qui représente une map et le convertir en un objet `Map` qui sera ensuite interprété par le gameview. Le gros du travail de la classe `Map` consiste à initialiser le navmesh. Pour ce faire on itère sur chaque subdivision de case et on y place un sommet de navmesh (si on n'est pas trop proche d'un buisson). Quand le blob devra calculer un chemin, c'est en fait la map qui le fait pour lui grâce à la méthode `calculate_path(self, start: arcade.Vec2, end: arcade.Vec2) -> list[arcade.Vec2]` qui renvoie la liste des nœuds par lesquels le blob devra passer.

# Gameview
Le gameview rassemble tous les éléments vus précédemment et représente le jeu dans son entièreté. Lors de son initialisation, il lit une map de classe `Map` et place les sprites aux endroits appropriés.
Dans la méthode `on_update(self) -> None`, appelée à chaque frame, se déroule tout le procédé logique du jeu.
On y fait par exemple bouger les entités, vérifier les collisions entre joueur et monstre, etc.
Cette méthode met à jour les éléments internes du jeu mais il faut également dessiner tout ce qu'il se passe.
On a donc la méthode `on_draw(self) -> None` aussi appelée à chaque frame qui dessine les sprites, ainsi que les éléments "GUI" du jeu.
