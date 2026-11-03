int item = 42;

int main()
{
    int values[2] = {1, 2};
    for (int item : values) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
        (void)item;
    }
    return item;
}
