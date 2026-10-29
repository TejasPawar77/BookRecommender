from rest_framework.decorators import api_view
from rest_framework.response import Response

from .recommendation import get_recommendations

@api_view(['GET'])
def recommend_books_api(request):
    query = request.query_params.get('search', '').strip()
    emotion = request.query_params.get('emotion')
    category = request.query_params.get('category')

    # print("API SEARCH PARAMETER:", repr(query))

    results = get_recommendations(
        query=query,
        emotion=emotion,
        category=category,
        top_n=10
    )

    # Prevent NoneType crashes if recommendations fail or return nothing
    if results is None:
        results = []

    return Response(results)