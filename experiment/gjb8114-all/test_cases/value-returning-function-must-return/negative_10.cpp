int update_counter(int counter)
{
    int increment = 3;
    counter += increment;
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]

int main()
{
    return update_counter(1);
}
