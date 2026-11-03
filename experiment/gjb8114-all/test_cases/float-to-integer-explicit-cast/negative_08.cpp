int main()
{
    float base = 1.75f;
    int total = 0;
    for (int i = base; i < 4; ++i) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
        total += i;
    }
    return total;
}
