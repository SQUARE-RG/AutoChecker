typedef struct S_Point
{
    int x;
    int y;
} Point;

int main()
{
    Point p{3, 4};
    return p.x + p.y;
}
