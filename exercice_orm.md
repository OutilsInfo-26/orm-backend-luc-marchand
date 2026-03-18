# Exercice : pratiquer ORM + SQL brut (FastAPI)

Objectif : étendre le mini projet ORM pour manipuler des requêtes SQL et ORM, tout en gardant la validation via schemas Pydantic.

---

## Questions de compréhension

Répondez aux questions suivantes avant de commencer l'implémentation.

### Base de données

1. Qu'est-ce qu'une clé primaire et à quoi sert-elle ?
   - Une clé primaire est un champ unique qui identifie de manière unique chaque enregistrement dans une table. Elle garantit l'unicité et l'intégrité des données.
2. Qu'est-ce qu'une clé étrangère ? Donnez un exemple avec les tables du projet.
   - Une clé étrangère est un champ qui fait référence à la clé primaire d'une autre table. Par exemple, `publisher_id` dans la table `Book` fait référence à `id` dans la table `Publisher`.
3. Quelle est la différence entre un `INNER JOIN` et un `LEFT JOIN` ? Quand utilise-t-on l'un plutôt que l'autre ?
   - Un `INNER JOIN` retourne uniquement les enregistrements qui ont des correspondances dans les deux tables. Un `LEFT JOIN` retourne tous les enregistrements de la table de gauche, même s'il n'y a pas de correspondance dans la table de droite.
4. Qu'est-ce qu'une table de jointure (association) ? Pourquoi en utilise-t-on une dans ce projet ?
   - Une table de jointure est une table intermédiaire utilisée pour représenter une relation N:M entre deux tables. Dans ce projet, la table `BookTag` est une table de jointure qui relie les livres et les tags, car un livre peut avoir plusieurs tags et un tag peut être associé à plusieurs livres.
5. Quelle est la différence entre une relation 1:N et une relation N:M ?
    - Une relation 1:N signifie qu'un enregistrement dans la table A peut être associé à plusieurs enregistrements dans la table B, mais chaque enregistrement dans la table B ne peut être associé qu'à un seul enregistrement dans la table A. Une relation N:M signifie que plusieurs enregistrements dans la table A peuvent être associés à plusieurs enregistrements dans la table B, nécessitant une table de jointure pour gérer ces associations.

### Modèles SQLAlchemy (`models.py`)

6. Pourquoi crée-t-on une classe `Base` qui hérite de `DeclarativeBase` au lieu d'hériter directement de `DeclarativeBase` dans chaque modèle ?
   - Créer une classe `Base` qui hérite de `DeclarativeBase` permet de centraliser la configuration commune à tous les modèles, comme les métadonnées. Cela facilite également la maintenance et l'extension du projet, car toute modification dans la classe `Base` affectera tous les modèles qui en héritent.
7. Comment sont créées les tables en base de données à partir des modèles Python ?
   - Les tables sont créées en base de données à partir des modèles Python en utilisant la méthode `Base.metadata.create_all(engine)`, qui lit les définitions des classes de modèle et génère les commandes SQL nécessaires pour créer les tables correspondantes dans la base de données.
8. Expliquez cette ligne :
   ```python
   id: Mapped[int] = mapped_column(primary_key=True)
   ```
   - Cette ligne définit un champ `id` de type entier qui est mappé à une colonne de la base de données. Le paramètre `primary_key=True` indique que ce champ est la clé primaire de la table, ce qui signifie qu'il doit être unique et non nul pour chaque enregistrement.
9.  Comment indique-t-on qu'un champ peut être `NULL` (optionnel) en base de données avec SQLAlchemy 2.0 ?
    - En SQLAlchemy 2.0, on peut indiquer qu'un champ peut être `NULL` en utilisant `mapped_column(nullable=True)`. Par défaut, les champs sont considérés comme `NOT NULL`, donc il est nécessaire de spécifier `nullable=True` pour permettre des valeurs nulles.
10. Expliquez cette ligne :
    ```python
    book_tags: Mapped[list["BookTag"]] = relationship("BookTag", back_populates="book")
    ```
    - Cette ligne définit une relation entre le modèle `Book` et le modèle `BookTag`. Le champ `book_tags` est une liste de `BookTag` associés à un livre. Le paramètre `back_populates="book"` indique que la relation est bidirectionnelle, ce qui signifie que dans le modèle `BookTag`, il doit y avoir un champ `book` qui fait référence à cette relation. Cela permet de naviguer facilement entre les deux modèles dans les requêtes ORM.
  
    Que signifie `back_populates` ? Que se passe-t-il si on l'omet ?
  - ça permet de créer une relation avec la classe `book` depuis `BookTag`. Grace à cela, on peut écrire `book.autor.name` pour accéder au nom de l'auteur d'un livre. Si on omet `back_populates`, la relation ne sera pas bidirectionnelle, ce qui signifie que vous ne pourrez pas accéder à l'objet lié depuis l'autre côté de la relation. Par exemple, si vous avez une relation entre `Book` et `Author`, sans `back_populates`, vous pourriez accéder à l'auteur d'un livre, mais pas aux livres d'un auteur.
  
11. Dans le modèle `Book`, `publisher_id` est défini comme `ForeignKey` mais il n'y a pas de `relationship` vers `Publisher`. Quelle conséquence cela a-t-il sur les requêtes ?
    - Cela signifie que vous ne pouvez pas accéder directement à l'objet `Publisher` à partir d'un objet `Book` en utilisant une relation ORM. Pour obtenir les informations du publisher d'un livre, vous devrez effectuer une jointure manuelle dans vos requêtes SQL ou ORM, plutôt que de pouvoir simplement accéder à `book.publisher.name` par exemple.

### Schemas Pydantic (`schemas.py`)

12. À quoi servent les schemas Pydantic dans ce projet ? Pourquoi ne retourne-t-on pas directement les objets SQLAlchemy ?
    - Les schemas Pydantic servent à définir la structure des données d'entrée et de sortie de l'API. Ils permettent de valider les données reçues et de contrôler la forme des données renvoyées. On ne retourne pas directement les objets SQLAlchemy car ils peuvent contenir des informations sensibles ou inutiles pour le client, et ils ne sont pas conçus pour être sérialisés en JSON. Les schemas Pydantic permettent de filtrer et de formater les données avant de les envoyer au client.
  
13. Dans `BookCreate`, expliquez le rôle des `...` dans `Field(...)` et celui de `min_length`, `max_length`.
    -  `Field(...)` indique que ce champ est obligatoire, tandis que `min_length` et `max_length` sont des contraintes de validation qui spécifient la longueur minimale et maximale de la chaîne de caractères.
14. Qu'est-ce que `model_config = {"from_attributes": True}` et dans quel cas est-ce nécessaire ?
    - `model_config = {"from_attributes": True}` est une configuration qui permet à Pydantic de créer un modèle à partir d'un objet SQLAlchemy en utilisant les attributs de l'objet. Cela est nécessaire lorsque vous souhaitez retourner des objets SQLAlchemy directement dans vos routes FastAPI, car cela permet à Pydantic de convertir automatiquement les objets SQLAlchemy en modèles Pydantic sans avoir à les convertir manuellement.
15. Quelle est la différence entre `BookCreate` et `BookOut` ? Pourquoi avoir deux schemas séparés ?
    - `BookCreate` est utilisé pour valider les données d'entrée lors de la création d'un livre, tandis que `BookOut` est utilisé pour définir la structure des données de sortie lorsqu'on retourne un livre dans une réponse. Avoir deux schemas séparés permet de contrôler précisément les champs qui sont requis pour la création d'un livre et ceux qui sont retournés au client, ce qui améliore la sécurité et la clarté de l'API.
16. Dans `AuthorUpdate`, tous les champs sont optionnels (`str | None`). Pourquoi ? Quelle est la différence avec `AuthorCreate` ?
    - Dans `AuthorUpdate`, tous les champs sont optionnels car lors de la mise à jour d'un auteur, il est possible de ne vouloir mettre à jour que certains champs, tandis que dans `AuthorCreate`, tous les champs sont requis pour créer un nouvel auteur.

### Routes FastAPI (`orm_simple.py`, `orm_join.py`, etc.)

17. Si le router est défini avec `prefix="/orm"`, pourquoi faut-il appeler `/orm/authors` et non `/authors` ?
    - Le `prefix="/orm"` dans le router signifie que tous les endpoints définis dans ce router seront préfixés par `/orm`. Par conséquent, pour accéder à la route qui liste les auteurs, il faut appeler `/orm/authors` au lieu de simplement `/authors`, car le préfixe est automatiquement ajouté à toutes les routes du router.
18. Quelle est la différence entre un paramètre de route et un paramètre de requête (query parameter) ? Donnez un exemple de chacun.
    - Un paramètre de route est une partie de l'URL qui est définie dans le chemin de la route et est généralement utilisé pour identifier une ressource spécifique. Par exemple, dans la route `/books/{book_id}`, `book_id` est un paramètre de route. Un paramètre de requête (query parameter) est une paire clé-valeur qui est ajoutée à la fin de l'URL après un point d'interrogation et est généralement utilisé pour filtrer ou modifier la réponse. Par exemple, dans l'URL `/books?author=John`, `author` est un paramètre de requête.
19. Pourquoi utilise-t-on `PATCH` pour la mise à jour d'un auteur plutôt que `PUT` ?
    - `PATCH` est utilisé pour les mises à jour partielles, ce qui signifie que vous pouvez envoyer uniquement les champs que vous souhaitez mettre à jour. En revanche, `PUT` est généralement utilisé pour les mises à jour complètes, où vous devez fournir tous les champs de l'objet, même ceux qui ne changent pas. Dans le cas de la mise à jour d'un auteur, il est plus flexible d'utiliser `PATCH` car cela permet de ne mettre à jour que certains champs sans avoir à renvoyer l'intégralité des données de l'auteur.
20. Que fait `payload.model_dump(exclude_unset=True)` dans la route de mise à jour ? Que se passerait-il sans `exclude_unset=True` ?
    - `payload.model_dump(exclude_unset=True)` convertit le modèle Pydantic en un dictionnaire tout en excluant les champs qui n'ont pas été définis dans la requête (c'est-à-dire les champs qui ont leur valeur par défaut). Sans `exclude_unset=True`, tous les champs du modèle seraient inclus dans le dictionnaire, même ceux qui n'ont pas été modifiés, ce qui pourrait entraîner la mise à jour de champs avec des valeurs par défaut non souhaitées.
21. Pourquoi utilise-t-on `session.get(Author, author_id)` plutôt que `session.execute(select(Author).where(Author.id == author_id))` pour chercher un élément par sa clé primaire ?
    - `session.get(Author, author_id)` est une méthode optimisée pour récupérer un enregistrement par sa clé primaire. Elle utilise une requête plus simple et plus rapide que `session.execute(select(Author).where(Author.id == author_id))`, qui est plus générique et peut être moins performant pour ce cas d'utilisation spécifique.

### ORM et requêtes

22. Expliquez la différence entre `session.add()` et `session.commit()`. Que se passe-t-il si on appelle `session.add()` sans `session.commit()` ?
    - `session.add()` ajoute un objet à la session, ce qui signifie qu'il est marqué pour être inséré dans la base de données lors du prochain commit. Cependant, tant que `session.commit()` n'est pas appelé, les changements ne sont pas persistés dans la base de données. Si on appelle `session.add()` sans `session.commit()`, l'objet sera ajouté à la session mais ne sera pas enregistré dans la base de données, et les autres sessions ou requêtes ne pourront pas voir cet objet.
23. À quoi sert `session.flush()` ? Dans quels cas l'utilise-t-on ?
    - `session.flush()` envoie les changements en attente à la base de données sans valider la transaction. Cela permet d'obtenir des valeurs générées par la base de données (comme les clés primaires auto-incrémentées) avant de faire un commit. On l'utilise souvent lorsque l'on a besoin de l'ID d'un objet nouvellement créé pour créer des relations avec d'autres objets dans la même session.
24. Expliquez la différence entre `joinedload` et `selectinload`. Dans quel cas préfère-t-on l'un à l'autre ?
    - `joinedload` effectue une jointure SQL pour charger les relations en une seule requête, ce qui peut être plus performant lorsque la relation est de type 1:N ou N:1 et que le nombre d'enregistrements liés est relativement faible. `selectinload`, en revanche, effectue une requête séparée pour charger les relations, ce qui peut être plus efficace lorsque la relation est de type N:M ou lorsque le nombre d'enregistrements liés est élevé, car cela évite de dupliquer les données dans la jointure. Le choix entre les deux dépend du contexte et de la structure des données.
25. Pourquoi dans FastAPI est-il quasi-obligatoire d'utiliser `selectinload`/`joinedload` lorsqu'on veut retourner des relations ? Que se passe-t-il si on ne le fait pas ?
    - Dans FastAPI, il est quasi-obligatoire d'utiliser `selectinload` ou `joinedload` pour charger les relations lorsque vous retournez des objets SQLAlchemy, car sinon vous risquez de rencontrer le problème de N+1. Si vous ne le faites pas, chaque accès à une relation non chargée entraînera une requête supplémentaire à la base de données, ce qui peut considérablement ralentir les performances de votre API, surtout si vous avez beaucoup d'enregistrements.
26. Quelle est la différence entre ces deux approches ?
    ```python
    # Approche A
    select(Book.id, Book.title, Author.name.label("author_name")).join(Author)

    # Approche B
    select(Book).options(joinedload(Book.author))
    ```
    - L'approche A utilise une jointure explicite pour sélectionner uniquement les champs nécessaires (id, title, author_name), ce qui peut être plus performant si vous n'avez besoin que de ces champs spécifiques. L'approche B utilise `joinedload` pour charger l'objet `Author` lié à chaque `Book`, ce qui vous permet d'accéder à tous les attributs de l'auteur, mais peut être moins performant si vous n'avez besoin que de quelques champs spécifiques. Le choix entre les deux dépend de vos besoins en termes de données et de performance.

---

## Tâches à réaliser

Les tâches suivantes sont à implémenter dans de nouveaux fichiers ou dans les fichiers existants selon la logique du projet.

### Modèle

#### 1. Table `Person`
Créez un modèle `Person` représentant le propriétaire d'un livre.

- Une personne peut posséder plusieurs livres
- Un livre appartient à une seule personne (relation 1:N)
- Attributs minimum : `id`, `first_name`, `last_name`
- Ajoutez le champ `owner_id` dans le modèle `Book` (avec ou sans `relationship`, à vous de choisir et de justifier)
- Ajoutez des données de test dans `init_db()`

### Routes — Persons

#### 2. Créer une personne
`POST /orm/persons`

- Valider les données avec un schema Pydantic
- Retourner la personne créée

#### 3. Lister les personnes
`GET /orm/persons`

- Retourner la liste de toutes les personnes

#### 4. Personnes avec leurs livres (nom seulement)
`GET /orm/persons-with-books`

- Retourner chaque personne avec la liste des titres de ses livres
- Ne pas retourner l'objet `Book` complet — uniquement le titre (string)
- Choisir la bonne stratégie de chargement et justifier votre choix

### Routes — Livres enrichis

#### 5. Livres avec auteur et éditeur
`GET /orm/books-full`

- Retourner chaque livre avec le nom de l'auteur et le nom de l'éditeur
- Rappel : `publisher_id` existe dans `Book` mais il n'y a pas de `relationship` — la jointure doit être faite manuellement

#### 6. Supprimer un livre
`DELETE /orm/books/{book_id}`

- Retourner `204 No Content` si supprimé
- Retourner `404` si le livre n'existe pas

### Routes — Statistiques

#### 7. Statistiques générales
`GET /orm/stats`

Retourner un objet JSON avec :
- Nombre total de livres
- Nombre total d'auteurs
- Nombre total de tags
- Titre et nombre de pages du livre le plus long
- Moyenne du nombre de pages de tous les livres

#### 8. Personnes avec le nombre de livres
`GET /orm/persons-with-book-count`

- Retourner chaque personne avec le nombre de livres qu'elle possède
- Utiliser une aggregation (`COUNT`) — pas de chargement de la liste des livres

---

## Validation avec PgAdmin

- Créez un fichier `validation.sql` avec des requêtes SQL pour vérifier que les données sont correctement insérées, mises à jour et supprimées dans la base de données
- Exécutez ces requêtes dans PgAdmin pour valider les opérations effectuées par votre API
- Contrôler que les jointures fonctionnent correctement en vérifiant les données retournées par les endpoints qui utilisent des jointures
- Contrôler les valeurs des statistiques retournées par les endpoints de statistiques

## Checklist de validation

- Les nouveaux endpoints apparaissent dans Swagger UI (`/docs`)
- Les validations Pydantic renvoient bien `422` si les données sont invalides
- Les routes `404` fonctionnent correctement
- Le `DELETE` retourne bien `204`
- Les statistiques affichent des valeurs correctes
- Les requêtes avec jointure ne font pas de N+1 (vérifier avec les logs SQL si disponible)
