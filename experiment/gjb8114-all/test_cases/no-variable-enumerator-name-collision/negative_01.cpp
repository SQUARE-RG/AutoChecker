enum Name_type { first = 0, second };

int main()
{
    unsigned int second = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
    Name_type e = first;
    (void)e;
    return static_cast<int>(second);
}
