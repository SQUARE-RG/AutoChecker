char* strcpy(char* dest, const char* src) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    char* start = dest;
    while (*src != '\0') {
        *dest = *src;
        ++dest;
        ++src;
    }
    *dest = '\0';
    return start;
}

int main()
{
    char buffer[8];
    strcpy(buffer, "abc");
    return buffer[0];
}
