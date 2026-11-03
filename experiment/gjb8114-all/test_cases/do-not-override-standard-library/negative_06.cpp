namespace std {
int strncmp(const char* lhs, const char* rhs, unsigned long count) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    while (count > 0 && *lhs != '\0' && *lhs == *rhs) {
        ++lhs;
        ++rhs;
        --count;
    }
    if (count == 0) {
        return 0;
    }
    return static_cast<unsigned char>(*lhs) - static_cast<unsigned char>(*rhs);
}
}

int main()
{
    return std::strncmp("abc", "abd", 3);
}
