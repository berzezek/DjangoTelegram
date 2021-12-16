from rest_framework.serializers import ModelSerializer

from kvint.models import Order, Profile


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class OrderSerializer(ModelSerializer):

    profile = ProfileSerializer()

    class Meta:
        model = Order
        fields = '__all__'
