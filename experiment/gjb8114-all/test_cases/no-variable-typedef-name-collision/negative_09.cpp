typedef unsigned long long Counter;

static Counter increment()
{
    static Counter Counter = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    return Counter + 1;
}

int main()
{
    return static_cast<int>(increment());
}
