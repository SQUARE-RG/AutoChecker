struct Point
{
    int x;
    int y;
};

int main()
{
    Point base{0, 0};
    Point *Point = &base; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    Point->x = 1;
    Point->y = 2;
    return base.x + base.y;
}
