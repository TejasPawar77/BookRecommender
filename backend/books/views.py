from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .recommendation import get_recommendations

@api_view(['GET'])
def recommend_books_api(request):
    """
    API Endpoint: /api/books/recommend/
    Query Parameters:
      - query: search term
      - emotion: filter by emotion
      - category: filter by category
      - limit: number of results (default: 10)
    """
    query = request.GET.get('query', '')
    emotion = request.GET.get('emotion', '')
    category = request.GET.get('category', '')
    
    try:
        limit = int(request.GET.get('limit', 10))
    except ValueError:
        limit = 10

    try:
        results = get_recommendations(
            query=query, 
            emotion=emotion, 
            category=category, 
            top_n=limit
        )
        return Response({
            "status": "success",
            "count": len(results),
            "data": results
        }, status=status.HTTP_200_OK)
    except FileNotFoundError as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)