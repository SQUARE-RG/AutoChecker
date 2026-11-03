// negative_04.cpp
// Pointer parameter name differs between prototype and definition.
int adjust(int* value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int main()
{
    int n = 5;
    return adjust(&n);
}

int adjust(int* data)
{
    return *data + 1;
}
