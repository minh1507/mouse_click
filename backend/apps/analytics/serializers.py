"""Serializers for the analytics app."""

from rest_framework import serializers
from .models import Heatmap, PathAnalysis, Funnel, FunnelStep, FunnelAnalysis

class HeatmapSerializer(serializers.ModelSerializer):
    """Serializer for Heatmap model."""
    class Meta:
        model = Heatmap
        fields = '__all__'

class PathAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for PathAnalysis model."""
    class Meta:
        model = PathAnalysis
        fields = '__all__'

class FunnelStepSerializer(serializers.ModelSerializer):
    """Serializer for FunnelStep model."""
    class Meta:
        model = FunnelStep
        fields = '__all__'

class FunnelSerializer(serializers.ModelSerializer):
    """Serializer for Funnel model."""
    steps = FunnelStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Funnel
        fields = '__all__'

class FunnelWithStepsSerializer(serializers.ModelSerializer):
    """Serializer for Funnel model with nested steps for creation/update."""
    steps = FunnelStepSerializer(many=True)
    
    class Meta:
        model = Funnel
        fields = '__all__'
    
    def create(self, validated_data):
        """Create a funnel with nested steps."""
        steps_data = validated_data.pop('steps')
        funnel = Funnel.objects.create(**validated_data)
        
        for step_data in steps_data:
            FunnelStep.objects.create(funnel=funnel, **step_data)
        
        return funnel
    
    def update(self, instance, validated_data):
        """Update a funnel with nested steps."""
        steps_data = validated_data.pop('steps')
        # Update funnel fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        # Clear existing steps and recreate
        instance.steps.all().delete()
        for step_data in steps_data:
            FunnelStep.objects.create(funnel=instance, **step_data)
        
        return instance

class FunnelAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for FunnelAnalysis model."""
    funnel_name = serializers.StringRelatedField(source='funnel.name', read_only=True)
    
    class Meta:
        model = FunnelAnalysis
        fields = '__all__' 