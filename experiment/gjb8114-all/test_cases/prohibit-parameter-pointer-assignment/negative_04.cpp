static int storage[4] = {10, 20, 30, 40};

int* obtain_buffer()
{
    return storage;
}

void rebind_pointer_parameter(int* p)
{
    p = obtain_buffer(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
}

int main()
{
    int value = 5;
    rebind_pointer_parameter(&value);
    return 0;
}
