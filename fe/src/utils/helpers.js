import clsx from 'clsx';

export const cn = clsx;

export const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatTime = (time) => {
  if (!time) return '';
  return new Date(`2000-01-01T${time}`).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDatetime = (datetime) => {
  if (!datetime) return '';
  return new Date(datetime).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getInitials = (firstName, lastName) => {
  return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
};

export const getTreatmentStatus = (status) => {
  const statuses = {
    pending: { color: 'warning', label: 'Pending' },
    in_progress: { color: 'info', label: 'In Progress' },
    completed: { color: 'success', label: 'Completed' },
    cancelled: { color: 'danger', label: 'Cancelled' },
  };
  return statuses[status] || statuses.pending;
};

export const truncate = (text, length = 50) => {
  if (!text) return '';
  return text.length > length ? `${text.substring(0, length)}...` : text;
};

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePhone = (phone) => {
  const re = /^[\d\s\-+()]+$/; // allow digits, spaces, hyphens, plus and parentheses
  return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
};

export const getAvatarColor = (index) => {
  const colors = [
    'bg-primary-500',
    'bg-pink-500',
    'bg-purple-500',
    'bg-indigo-500',
    'bg-blue-500',
    'bg-cyan-500',
    'bg-teal-500',
    'bg-green-500',
  ];
  return colors[index % colors.length];
};
