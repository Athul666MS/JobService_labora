from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    # Comes from User/Auth Service (JWT)
    client_id = models.IntegerField()

    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="jobs")

    budget_min = models.DecimalField( max_digits=10,decimal_places=2)
    budget_max = models.DecimalField( max_digits=10, decimal_places=2 )

    deadline = models.DateField()

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="open")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
