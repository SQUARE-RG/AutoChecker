// Dangling-else: the inner if-else-if chain has no final else branch.
int choose(int a, int b, int c)
{
    int x = -1;
    if (a) if (b) x = 1; else if (c) x = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
    return x;
}

int main()
{
    return choose(1, 0, 0);
}
