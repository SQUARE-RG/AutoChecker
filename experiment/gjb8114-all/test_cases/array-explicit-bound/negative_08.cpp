constexpr int values[] = {1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]

int main()
{
    return values[0] + values[1] + values[2];
}
