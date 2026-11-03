namespace {
    unsigned long strlen(const char* text)
    {
        unsigned long length = 0;
        while (text[length] != '\0') {
            ++length;
        }
        return length;
    }
}

int main()
{
    const char* message = "hello";
    unsigned long length = strlen(message);
    return length == 5 ? 0 : 1;
}
