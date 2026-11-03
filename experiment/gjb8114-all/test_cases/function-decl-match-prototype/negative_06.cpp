long combine(int left, int right); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

long combine(int left, long right)
{
    return static_cast<long>(left) + right;
}

int main()
{
    return combine(1, 2L) == 3 ? 0 : 1;
}
