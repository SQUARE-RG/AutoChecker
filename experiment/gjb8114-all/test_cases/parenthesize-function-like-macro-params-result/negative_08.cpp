struct Point { int x; int y; };

#define GET_X(pt) (pt).x // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    Point p{1, 2};
    int value = GET_X(p) + 1;
    return value;
}
