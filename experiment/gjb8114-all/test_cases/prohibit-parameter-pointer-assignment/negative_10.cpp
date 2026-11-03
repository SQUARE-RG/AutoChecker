static int* g_slot = nullptr;

void rebind_slot(int** pp)
{
    pp = &g_slot; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
}

int main()
{
    int* local_slot = nullptr;
    rebind_slot(&local_slot);
    return 0;
}
