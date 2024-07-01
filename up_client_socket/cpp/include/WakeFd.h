#pragma once

#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <string>

class WakeFd {
	int fd_;
	int pair_[2];

public:
	WakeFd(int fd) : fd_(fd) { auto pret = pipe(pair_); }

	~WakeFd() {
		close(fd_);
		close(pair_[0]);
		close(pair_[1]);
	}

	int fd() { return fd_; }

	void wake() {
		int dummy;
		auto ret = write(pair_[1], &dummy, sizeof(dummy));
	}

	bool read(std::string& data) {
		struct pollfd fds[2];
		fds[0].fd = fd_;
		fds[0].events = POLLIN;
		fds[0].revents = 0;
		fds[1].fd = pair_[0];
		fds[1].events = POLLIN;
		fds[1].revents = 0;
		int ret = poll(fds, 2, -1);
		if (fds[1].revents)
			return false;
		if (fds[0].revents == 0) {
			data.resize(0);
			return true;
		}
		data.reserve(326768);
		int readSize = ::read(fd_, data.data(), 32768);
		if (readSize < 0)
			return false;
		data.resize(readSize);
		return true;
	}

	template <typename... Params>
	int send(Params&&... params) {
		return ::send(fd_, std::forward<Params>(params)...);
	}

	template <typename... Params>
	int connect(Params&&... params) {
		return ::connect(fd_, std::forward<Params>(params)...);
	}
};