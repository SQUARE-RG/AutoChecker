struct Point
{
    int x;
    int y;
};

int main()
{
    Point p{0, 0};
    double value = 3.75;
    p.x = static_cast<int>(value);
    return p.x;
}
