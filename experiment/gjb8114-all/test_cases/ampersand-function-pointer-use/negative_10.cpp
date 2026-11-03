using Fn = int (*)(int, int);

int subtract(int a, int b) { return a - b; }

int main()
{
    Fn* fp = new Fn(subtract); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
    int result = (*fp)(5, 3);
    delete fp;
    return result == 2 ? 0 : 1;
}
