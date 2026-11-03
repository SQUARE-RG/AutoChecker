// negative_05.cpp
#define BEGIN_EXTERN_C extern "C" { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

BEGIN_EXTERN_C
int c_add_one(int x)
{
    return x + 1;
}
}

int main()
{
    return c_add_one(41) == 42 ? 0 : 1;
}
