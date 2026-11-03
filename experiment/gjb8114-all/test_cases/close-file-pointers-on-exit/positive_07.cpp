#include <cstdio>

class FileGuard
{
public:
    explicit FileGuard(std::FILE* file) : file_(file) {}
    ~FileGuard() { if (file_ != nullptr) std::fclose(file_); }
    FileGuard(const FileGuard&) = delete;
    FileGuard& operator=(const FileGuard&) = delete;
    std::FILE* get() const { return file_; }
private:
    std::FILE* file_;
};

int read_data()
{
    std::FILE* fp = std::fopen("data.txt", "r");
    if (fp == nullptr) {
        return -1;
    }
    FileGuard guard(fp);
    std::FILE* handle = guard.get();
    char buffer[64];
    if (std::fgets(buffer, sizeof(buffer), handle) == nullptr) {
        return -2;
    }
    return 0;
}

int main()
{
    return read_data();
}
