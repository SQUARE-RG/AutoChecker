struct Vec2
{
    double x;
    double y;
};

#define VEC Vec2

int main()
{
    VEC v{1.0, 2.0};
    return static_cast<int>(v.x);
}
