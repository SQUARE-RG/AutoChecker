#include <string>

/* Build a greeting for the given name. */
std::string greet(const std::string& name) {
    return "Hello, " + name; /* return the greeting text */
}

int main() {
    std::string result = greet("world");
    return result.empty() ? 1 : 0; /* report success */
}
