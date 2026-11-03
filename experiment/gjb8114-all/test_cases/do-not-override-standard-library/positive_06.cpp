class CStringComparer {
public:
    int strncmp(const char* lhs, const char* rhs, unsigned long count) const
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
};

int main()
{
    CStringComparer comparer;
    return comparer.strncmp("abc", "abd", 3);
}
