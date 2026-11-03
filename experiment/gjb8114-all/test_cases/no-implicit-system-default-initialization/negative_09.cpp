template <typename T>
T shared_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]

int main()
{
    shared_value<int> = 1;
    return 0;
}
