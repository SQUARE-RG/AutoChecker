struct Point
{
    int x;
    int y;
};

int main()
{
    Point point{1, 2};
    point.x; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return 0;
}
