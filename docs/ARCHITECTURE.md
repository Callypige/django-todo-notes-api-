# Architecture et Décisions Techniques

Documentation des choix d'architecture du projet Django Todo & Notes REST API.

## Principes directeurs

- **Séparation des responsabilités** - Chaque app gère son domaine
- **Couplage faible** - Communication via ORM, pas d'imports croisés
- **Convention over configuration** - Standards Django/DRF
- **Testabilité** - 52 tests automatisés

## Choix majeurs

### 1. Deux apps distinctes (`notes` et `todos`)

**Pourquoi ?**
- Modularité : chaque app évolue indépendamment
- Responsabilité unique : Notes ≠ Todos
- Réutilisabilité : `todos` peut être réutilisé ailleurs

**Alternative rejetée :** Une seule app monolithique
- ❌ Couplage fort, moins de flexibilité

### 2. ForeignKey avec `related_name='todos'`

```python
class Todo(models.Model):
    note = models.ForeignKey('notes.Note', related_name='todos', 
                              on_delete=models.SET_NULL, null=True)
```

**Pourquoi ?**
- Accès intuitif : `note.todos.all()`
- Performance : optimisations ORM (`select_related`)
- `SET_NULL` : suppression note → déliaison (pas de cascade)

**Alternative rejetée :** `ManyToMany`
- ❌ Complexité inutile (une todo = une seule note)

### 3. Signaux Django pour synchronisation des statuts

```python
@receiver(post_save, sender=Todo)
def update_note_status_on_todo_save(sender, instance, **kwargs):
    if instance.note:
        instance.note.update_status_from_todos()
```

**Pourquoi ?**
- Automatique : aucun code dans les vues
- Centralisé : logique dans le modèle
- Découplage : `notes` n'importe pas `todos`
- Fonctionne partout : shell, admin, API

**Alternative rejetée :** Override `save()` dans `TodoSerializer`
- ❌ Logique métier dans la présentation
- ❌ Ne fonctionne pas en bulk ou shell

**Trade-off :** Les signaux peuvent être difficiles à déboguer → solution : tests complets

### 4. Validation métier dans `delete()` du modèle

```python
def delete(self, *args, **kwargs) -> None:
    if self.todos.exists():
        raise ValidationError("Cannot delete note with existing todos")
    super().delete(*args, **kwargs)
```

**Pourquoi ?**
- Intégrité garantie (pas de todos orphelines)
- Fonctionne partout (API, shell, admin)

**Alternative rejetée :** `on_delete=CASCADE`
- ❌ Perte de données dangereuse

### 5. Django REST Framework avec ViewSets

```python
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [SearchFilter, OrderingFilter]
```

**Pourquoi ?**
- Code minimal, très lisible
- CRUD automatique
- Pagination/filtres par défaut

**Alternative rejetée :** APIView
- ❌ Beaucoup plus de code

## Trade-offs clés

### Signaux vs Celery

| Critère | Signaux (choisi) | Celery |
|---------|------------------|--------|
| Complexité | ✅ Simple | ❌ Redis + worker |
| Performance | ✅ OK <1000 todos | ✅ Scalable |
| Temps réel | ✅ Immédiat | ❌ Latence |

**Conclusion :** Signaux suffisent pour ce use case

### Enum vs Strings

```python
class NoteStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    IN_PROGRESS = 'in_progress', 'In Progress'
```

**Avantages Enum :**
- ✅ Type safety + autocomplete
- ✅ Validation automatique
- ✅ Centralisé

### Pagination activée par défaut

20 items/page pour éviter timeouts et respecter les best practices REST.

## Performance

**Optimisations actuelles :**
- Pagination (20/page)
- Index auto sur `created_at`, `updated_at`
- Lazy loading ORM

**Pour scaler :**
- `annotate(todos_count=Count('todos'))` pour éviter N+1
- Cache Redis sur `GET /notes/{id}/`
- Index composites `(status, -created_at)`
- Read replicas PostgreSQL

## Conclusion

Choix **pragmatiques** :
- Simplicité (conventions Django/DRF)
- Maintenabilité (tests, type hints)
- Évolutivité (apps modulaires)

Pas de sur-ingénierie, mais base solide pour évoluer.
