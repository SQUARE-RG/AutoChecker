struct Point { int x; int y; };

#define GET_X(pt) ((pt).x)

int main()
{
    Point p{1, 2};
    int value = GET_X(p) + 1;
    return value;
}
