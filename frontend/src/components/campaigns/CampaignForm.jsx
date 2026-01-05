import React, { useState } from 'react'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'

const CampaignForm = ({ onSubmit, onCancel, initialData = null }) => {
  const [formData, setFormData] = useState(
    initialData || {
      name: '',
      type: 'Newsletter',
      subject: '',
      description: '',
      scheduled_date: '',
    }
  )

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Campaign Name"
        name="name"
        value={formData.name}
        onChange={handleChange}
        required
      />

      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          Campaign Type
        </label>
        <select
          name="type"
          value={formData.type}
          onChange={handleChange}
          className="input"
          required
        >
          <option value="Newsletter">Newsletter</option>
          <option value="Promotional">Promotional</option>
          <option value="Welcome Series">Welcome Series</option>
          <option value="Abandoned Cart">Abandoned Cart</option>
          <option value="Win-Back">Win-Back</option>
        </select>
      </div>

      <Input
        label="Subject Line"
        name="subject"
        value={formData.subject}
        onChange={handleChange}
        required
      />

      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="input"
        />
      </div>

      <Input
        label="Scheduled Date"
        name="scheduled_date"
        type="datetime-local"
        value={formData.scheduled_date}
        onChange={handleChange}
      />

      <div className="flex space-x-3">
        <Button type="submit" className="flex-1">
          {initialData ? 'Update Campaign' : 'Create Campaign'}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

export default CampaignForm
