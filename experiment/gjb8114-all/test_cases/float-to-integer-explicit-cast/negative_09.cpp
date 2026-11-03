struct Point
{
    int x;
    int y;
};

int main()
{
    Point p{0, 0};
    double value = 3.75;
    p.x = value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return p.x;
}
