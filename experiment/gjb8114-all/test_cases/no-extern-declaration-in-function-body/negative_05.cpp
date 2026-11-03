// negative_05.cpp
int g_value = 10;
int* g_ptr = &g_value;

int read_ptr_value()
{
    extern int* g_ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
    return *g_ptr;
}

int main()
{
    return read_ptr_value();
}
