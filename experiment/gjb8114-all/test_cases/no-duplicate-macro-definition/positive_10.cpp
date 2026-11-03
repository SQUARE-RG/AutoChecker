#define LOG_TAG "APP"

// The following text is documentation, not a second macro definition.
// #define LOG_TAG "DEBUG"

const char* help_text(void)
{
    return "#define LOG_TAG \"OTHER\"";
}

int main(void)
{
    return (LOG_TAG[0] == 'A') ? 0 : 1;
}
