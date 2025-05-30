"""Models for the analytics app."""

from django.db import models
from apps.tracking.models import Session, Event

class Heatmap(models.Model):
    """Model to store processed heatmap data."""
    HEATMAP_TYPES = (
        ('click', 'Click Heatmap'),
        ('move', 'Movement Heatmap'),
    )
    
    name = models.CharField(max_length=100)
    url_pattern = models.CharField(max_length=255)
    heatmap_type = models.CharField(max_length=10, choices=HEATMAP_TYPES)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict)
    resolution_width = models.IntegerField(default=1920)
    resolution_height = models.IntegerField(default=1080)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_heatmap_type_display()} - {self.name}"
    
    class Meta:
        indexes = [
            models.Index(fields=['url_pattern']),
            models.Index(fields=['heatmap_type']),
            models.Index(fields=['date_from', 'date_to']),
        ]

class PathAnalysis(models.Model):
    """Model to store path analysis data."""
    name = models.CharField(max_length=100)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Path Analysis - {self.name}"

class FunnelStep(models.Model):
    """Model to represent a step in a funnel analysis."""
    name = models.CharField(max_length=100)
    url_pattern = models.CharField(max_length=255)
    step_order = models.IntegerField()
    funnel = models.ForeignKey('Funnel', on_delete=models.CASCADE, related_name='steps')
    
    def __str__(self):
        return f"{self.funnel.name} - Step {self.step_order}: {self.name}"
    
    class Meta:
        ordering = ['step_order']

class Funnel(models.Model):
    """Model to store funnel analysis configuration."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class FunnelAnalysis(models.Model):
    """Model to store funnel analysis results."""
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='analyses')
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Funnel Analysis - {self.funnel.name} ({self.date_from} to {self.date_to})" 