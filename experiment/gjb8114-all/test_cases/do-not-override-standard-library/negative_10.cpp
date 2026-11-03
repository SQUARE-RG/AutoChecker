namespace std {
    long int strtol(const char* text, char** endptr, int base) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
    {
        (void)endptr;
        long int value = 0;
        for (const char* p = text; *p >= '0' && *p <= '9'; ++p) {
            value = value * base + (*p - '0');
        }
        return value;
    }
}

int main() {
    const char* number = "123";
    long int parsed = std::strtol(number, nullptr, 10);
    return parsed == 123 ? 0 : 1;
}
